from __future__ import annotations

import csv
import io
from typing import List, Dict, Any

from django import forms
from django.contrib import messages
from django.utils.translation import gettext as _

from .models import Subscriber, Subscription, SubscriptionList


class SubscriberImportForm(forms.Form):
    """Form for bulk importing subscribers."""
    
    csv_file = forms.FileField(
        label=_("CSV File"),
        help_text=_("Upload a CSV file with columns: email, first_name, last_name, list_slug (optional)")
    )
    subscription_list = forms.ModelChoiceField(
        queryset=SubscriptionList.objects.all(),
        label=_("Default Subscription List"),
        help_text=_("If list_slug column is not provided, all subscribers will be added to this list"),
        required=False
    )
    skip_existing = forms.BooleanField(
        label=_("Skip Existing Subscribers"),
        help_text=_("If checked, existing subscribers will be skipped"),
        initial=True,
        required=False
    )
    send_confirmation = forms.BooleanField(
        label=_("Send Confirmation Emails"),
        help_text=_("If checked, confirmation emails will be sent to new subscribers"),
        initial=True,
        required=False
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        # Check file extension
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError(_("Please upload a CSV file."))
        
        # Check file size (max 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError(_("File size must be less than 5MB."))
        
        # Try to read and validate CSV
        try:
            csv_file.seek(0)
            content = csv_file.read().decode('utf-8')
            csv_file.seek(0)  # Reset file pointer
            
            # Check if CSV has required columns
            reader = csv.DictReader(io.StringIO(content))
            if not reader.fieldnames or 'email' not in reader.fieldnames:
                raise forms.ValidationError(_("CSV must contain an 'email' column."))
            
            # Validate email addresses
            email_errors = []
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                if not row.get('email', '').strip():
                    email_errors.append(f"Row {row_num}: Empty email address")
                    continue
                    
                email = row['email'].strip()
                if '@' not in email:
                    email_errors.append(f"Row {row_num}: Invalid email format '{email}'")
            
            if email_errors:
                raise forms.ValidationError(_("CSV validation errors:\n") + "\n".join(email_errors[:10]))
                
        except UnicodeDecodeError:
            raise forms.ValidationError(_("Please upload a valid UTF-8 encoded CSV file."))
        except Exception as e:
            raise forms.ValidationError(_("Error reading CSV file: ") + str(e))
        
        return csv_file
    
    def clean(self):
        cleaned_data = super().clean()
        subscription_list = cleaned_data.get('subscription_list')
        
        # If no default list is selected, check if CSV has list_slug column
        if not subscription_list:
            csv_file = cleaned_data.get('csv_file')
            if csv_file:
                csv_file.seek(0)
                content = csv_file.read().decode('utf-8')
                csv_file.seek(0)
                
                reader = csv.DictReader(io.StringIO(content))
                if 'list_slug' not in reader.fieldnames:
                    raise forms.ValidationError(_(
                        "Either select a default subscription list or include 'list_slug' column in CSV."
                    ))
        
        return cleaned_data


def process_subscriber_import(
    csv_file, 
    subscription_list=None, 
    skip_existing=True, 
    send_confirmation=True
) -> Dict[str, int]:
    """Process the CSV import and return statistics."""
    
    stats = {
        'imported': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': []
    }
    
    csv_file.seek(0)
    content = csv_file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    
    for row_num, row in enumerate(reader, start=2):
        try:
            email = row['email'].strip().lower()
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            list_slug = row.get('list_slug', '').strip()
            
            if not email:
                stats['errors'] += 1
                stats['error_details'].append(f"Row {row_num}: Empty email")
                continue
            
            # Determine which subscription list to use
            target_list = None
            if list_slug:
                try:
                    target_list = SubscriptionList.objects.get(slug=list_slug)
                except SubscriptionList.DoesNotExist:
                    stats['errors'] += 1
                    stats['error_details'].append(f"Row {row_num}: List '{list_slug}' not found")
                    continue
            elif subscription_list:
                target_list = subscription_list
            else:
                stats['errors'] += 1
                stats['error_details'].append(f"Row {row_num}: No subscription list specified")
                continue
            
            # Check if subscriber already exists
            subscriber, created = Subscriber.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                }
            )
            
            if not created and skip_existing:
                # Update name if provided and different
                updated = False
                if first_name and first_name != subscriber.first_name:
                    subscriber.first_name = first_name
                    updated = True
                if last_name and last_name != subscriber.last_name:
                    subscriber.last_name = last_name
                    updated = True
                if updated:
                    subscriber.save()
            
            # Check if subscription already exists
            subscription, sub_created = Subscription.objects.get_or_create(
                subscriber=subscriber,
                subscription_list=target_list,
                defaults={
                    'opt_in_source': 'csv_import',
                    'status': Subscription.Status.PENDING if target_list.double_opt_in else Subscription.Status.ACTIVE,
                }
            )
            
            if not sub_created and skip_existing:
                stats['skipped'] += 1
                continue
            
            # Send confirmation if requested and double opt-in is enabled
            if send_confirmation and target_list.double_opt_in and sub_created:
                from .tasks import send_confirmation
                send_confirmation.delay(subscription.pk)
            
            stats['imported'] += 1
            
        except Exception as e:
            stats['errors'] += 1
            stats['error_details'].append(f"Row {row_num}: {str(e)}")
    
    return stats

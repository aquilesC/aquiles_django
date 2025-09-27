from __future__ import annotations

from typing import Iterable, Optional

from django import forms

from .models import SubscriptionList


class SubscriptionForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}))
    first_name = forms.CharField(label="First name", max_length=150, required=False)
    last_name = forms.CharField(label="Last name", max_length=150, required=False)
    lists = forms.ModelMultipleChoiceField(queryset=SubscriptionList.objects.none())
    next = forms.CharField(widget=forms.HiddenInput(), required=False)
    source = forms.CharField(widget=forms.HiddenInput(), required=False)
    success_message = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(
        self,
        *args,
        available_lists: Optional[Iterable[SubscriptionList]] = None,
        show_name_fields: bool = True,
        allow_multiple: bool = False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if available_lists is None:
            available_lists = SubscriptionList.objects.filter(is_public=True)
        self.available_lists = list(available_lists)
        self.fields["lists"].queryset = SubscriptionList.objects.filter(pk__in=[lst.pk for lst in self.available_lists])
        field_css = "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        self.fields["email"].widget.attrs.setdefault("class", field_css)
        self.fields["first_name"].widget.attrs.setdefault("class", field_css)
        self.fields["last_name"].widget.attrs.setdefault("class", field_css)
        if not allow_multiple or len(self.available_lists) == 1:
            self.fields["lists"].widget = forms.MultipleHiddenInput()
            initial_ids = [lst.pk for lst in self.available_lists[:1]]
            self.initial.setdefault("lists", initial_ids)
        else:
            self.fields["lists"].widget = forms.CheckboxSelectMultiple()
        if not show_name_fields:
            self.fields["first_name"].widget = forms.HiddenInput()
            self.fields["last_name"].widget = forms.HiddenInput()

    def clean_lists(self):
        lists = self.cleaned_data["lists"]
        if not lists:
            raise forms.ValidationError("Please choose at least one list")
        return lists


class UnsubscribeForm(forms.Form):
    confirm = forms.BooleanField(label="Yes, unsubscribe me")
    reason = forms.CharField(label="Reason (optional)", widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reason"].widget.attrs.setdefault(
            "class",
            "mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500",
        )
        self.fields["confirm"].widget.attrs.setdefault("class", "h-4 w-4 text-red-600 border-gray-300 rounded")

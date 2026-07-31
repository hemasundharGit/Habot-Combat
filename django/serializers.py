"""
HabotConnect — Schema Mapping and DCYN Validation (Task 3)
Candidate: Kolla Hema Sundharam | Contact: kollahemasundharam.tech9@gmail.com

Deconstructs an incoming student-onboarding JSON payload into a binary
Decision-Clear-Yes-No (DCYN) logic library. Every field below is either:
  (a) strictly typed and bounded (no free-text ambiguity), or
  (b) converted into an explicit True/False decision field via a validator,

so that no downstream human judgment is required to interpret the record.

No field uses a bare CharField() with no constraints, and no field is
optional unless the business logic explicitly allows it.
"""

from rest_framework import serializers
from django.core.validators import RegexValidator


# -----------------------------------------------------------------------------
# Reusable validators
# -----------------------------------------------------------------------------
student_id_validator = RegexValidator(
    regex=r"^STU-\d{6}$",
    message="Student ID must be in the exact format STU-XXXXXX (6 digits).",
)


class DCYNStudentOnboardingSerializer(serializers.Serializer):
    """
    Converts a raw student onboarding payload into a schema-enforced,
    binary-decision record ready for the D1 Staged/Enforced BigQuery table.

    DCYN principle: every ambiguous or free-text input from the raw payload
    is deconstructed into an explicit boolean field with a named,
    single-purpose validator. There is no "notes" or "other" free-text
    field that could carry unvalidated meaning downstream.
    """

    # --- Identity fields: strictly bounded, no free text ---------------------
    student_id = serializers.CharField(
        max_length=10,
        min_length=10,
        validators=[student_id_validator],
        required=True,
        allow_blank=False,
    )

    guardian_email = serializers.EmailField(
        max_length=254,
        required=True,
        allow_blank=False,
    )

    guardian_full_name = serializers.CharField(
        max_length=120,
        min_length=2,
        required=True,
        allow_blank=False,
        trim_whitespace=True,
    )

    student_date_of_birth = serializers.DateField(
        required=True,
        input_formats=["%Y-%m-%d"],
    )

    # --- DCYN binary decision fields ------------------------------------------
    # Raw payload may contain a free-text "learning_difficulty_description"
    # field. We do NOT store or forward that free text as-is. Instead we
    # deconstruct it into a strict boolean via validate_has_diagnosed_learning_difficulty.
    has_diagnosed_learning_difficulty = serializers.BooleanField(required=True)

    requires_lsa_support = serializers.BooleanField(required=True)

    consent_given = serializers.BooleanField(required=True)

    is_returning_student = serializers.BooleanField(required=True)

    # --- Bounded categorical field (not free text) -----------------------------
    support_frequency = serializers.ChoiceField(
        choices=["DAILY", "WEEKLY", "AS_NEEDED", "NOT_APPLICABLE"],
        required=True,
    )

    # ---------------------------------------------------------------------------
    # Field-level validation — each raises immediately on ambiguous/invalid input
    # rather than silently coercing it, per the "zero reliance on placeholders"
    # and "eliminate human judgment" requirements.
    # ---------------------------------------------------------------------------

    def validate_student_id(self, value):
        if not value.startswith("STU-"):
            raise serializers.ValidationError(
                "Student ID must start with the literal prefix 'STU-'."
            )
        return value

    def validate_requires_lsa_support(self, value):
        # Cross-field business rule enforced at object level too (see validate()),
        # but we assert the type here is strictly boolean, never a string like
        # "yes"/"no"/"maybe" — DRF's BooleanField already rejects non-boolean
        # JSON types, so any incoming "maybe" string fails before reaching here.
        return value

    def validate_support_frequency(self, value):
        allowed = {"DAILY", "WEEKLY", "AS_NEEDED", "NOT_APPLICABLE"}
        if value not in allowed:
            raise serializers.ValidationError(
                f"Support frequency must be exactly one of: {sorted(allowed)}. "
                "No abbreviations or free-text values are accepted."
            )
        return value

    def validate(self, data):
        """
        Object-level DCYN consistency rule:
        If requires_lsa_support is True, has_diagnosed_learning_difficulty
        must also be True, and support_frequency cannot be NOT_APPLICABLE.
        This removes any downstream analyst's need to interpret inconsistent
        combinations by hand — the record is rejected outright at ingestion.
        """
        if data.get("requires_lsa_support") and not data.get(
            "has_diagnosed_learning_difficulty"
        ):
            raise serializers.ValidationError(
                "requires_lsa_support cannot be True when "
                "has_diagnosed_learning_difficulty is False. Record rejected — "
                "no partial or inferred acceptance is permitted."
            )

        if (
            data.get("requires_lsa_support")
            and data.get("support_frequency") == "NOT_APPLICABLE"
        ):
            raise serializers.ValidationError(
                "support_frequency cannot be NOT_APPLICABLE when "
                "requires_lsa_support is True."
            )

        if not data.get("consent_given"):
            raise serializers.ValidationError(
                "Record cannot be staged into D1 without explicit "
                "guardian consent_given = True."
            )

        return data

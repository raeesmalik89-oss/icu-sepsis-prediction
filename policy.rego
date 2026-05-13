
package icu.auth

default allow = false

allow if {
    input.role == "doctor"
    input.action == "read"
}

allow if {
    input.role == "nurse"
    input.action == "read"
    input.patient_id == input.user_assigned_patient
}

allow if {
    input.role == "admin"
}

allow if {
    input.role == "researcher"
    input.action == "read_anonymized"
}

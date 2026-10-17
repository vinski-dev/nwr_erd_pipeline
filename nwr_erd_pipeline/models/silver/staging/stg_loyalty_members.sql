select
    member_no,
    first_name,
    last_name,
    email,
    cast(dob as date) as dob,
    tier,
    cast(enroll_date as date) as enroll_date,
    _loaded_at
from {{ source('bronze', 'loyalty_members') }}

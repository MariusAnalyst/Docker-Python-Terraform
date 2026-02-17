with trips_unioned as (
    select * from {{ ref('int_trip_union') }}
),

vendors as (
    select 
        distinct vendor_id,
        {{ get_vendor_data('vendor_id') }} as vendor_name
        from trips_unioned
)

select * from vendors
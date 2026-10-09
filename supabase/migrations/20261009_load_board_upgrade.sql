-- صلایان بار نیمبلوک
-- اجرای یک‌باره در Supabase Dashboard > SQL Editor
-- این migration ستون‌های اختیاری موردنیاز تالار حرفه‌ای بار را اضافه می‌کند.
-- سیاست‌های دسترسی (RLS) فعلی عمداً تغییر داده نمی‌شوند.

alter table public.loads
  add column if not exists fare numeric(14,0),
  add column if not exists truck_type text,
  add column if not exists body_type text,
  add column if not exists loading_time timestamptz,
  add column if not exists note text,
  add column if not exists latitude double precision,
  add column if not exists longitude double precision,
  add column if not exists distance_km numeric(9,2);

create index if not exists loads_status_created_at_idx
  on public.loads (status, created_at desc);

create index if not exists loads_origin_destination_idx
  on public.loads (origin, destination);

comment on column public.loads.fare is 'کرایه اعلام‌شده به تومان؛ مقدار واقعی باید از اعلام‌کننده بار ثبت شود.';
comment on column public.loads.truck_type is 'نوع کامیون موردنیاز';
comment on column public.loads.body_type is 'نوع اتاق یا کاربری ناوگان';
comment on column public.loads.loading_time is 'زمان بارگیری';
comment on column public.loads.note is 'توضیحات اعلام‌کننده بار';
comment on column public.loads.latitude is 'عرض جغرافیایی مبدأ بار، در صورت ثبت و اعتبارسنجی';
comment on column public.loads.longitude is 'طول جغرافیایی مبدأ بار، در صورت ثبت و اعتبارسنجی';
comment on column public.loads.distance_km is 'فاصله تقریبی ذخیره‌شده بر حسب کیلومتر، در صورت معتبر بودن منبع';

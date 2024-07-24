def is_even(x):
  # تحديد ما إذا كان الرقم زوجيًا.
  if x % 2 == 0:
    return True
  return False
# قائمة من الأعداد
number = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# تصفية الاعداد الزوجية فقط
even_number = list(filter(is_even, number))
# طباعة الاعداد الزوجية
print(even_number)

define i64 @kernel(i64 %x) {
entry:
  %s32 = lshr i64 %x, 32
  %x32 = xor i64 %x, %s32
  %s16 = lshr i64 %x32, 16
  %x16 = xor i64 %x32, %s16
  %s8 = lshr i64 %x16, 8
  %x8 = xor i64 %x16, %s8
  %s4 = lshr i64 %x8, 4
  %x4 = xor i64 %x8, %s4
  %s2 = lshr i64 %x4, 2
  %x2 = xor i64 %x4, %s2
  %s1 = lshr i64 %x2, 1
  %x1 = xor i64 %x2, %s1
  %r = and i64 %x1, 1
  ret i64 %r
}

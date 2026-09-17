define i64 @kernel(i64 %x) {
entry:
  %b0 = and i64 %x, 255
  %b0s = shl i64 %b0, 56
  %s1 = lshr i64 %x, 8
  %b1 = and i64 %s1, 255
  %b1s = shl i64 %b1, 48
  %s2 = lshr i64 %x, 16
  %b2 = and i64 %s2, 255
  %b2s = shl i64 %b2, 40
  %s3 = lshr i64 %x, 24
  %b3 = and i64 %s3, 255
  %b3s = shl i64 %b3, 32
  %s4 = lshr i64 %x, 32
  %b4 = and i64 %s4, 255
  %b4s = shl i64 %b4, 24
  %s5 = lshr i64 %x, 40
  %b5 = and i64 %s5, 255
  %b5s = shl i64 %b5, 16
  %s6 = lshr i64 %x, 48
  %b6 = and i64 %s6, 255
  %b6s = shl i64 %b6, 8
  %b7 = lshr i64 %x, 56
  %r01 = or i64 %b0s, %b1s
  %r012 = or i64 %r01, %b2s
  %r0123 = or i64 %r012, %b3s
  %r01234 = or i64 %r0123, %b4s
  %r012345 = or i64 %r01234, %b5s
  %r0123456 = or i64 %r012345, %b6s
  %r = or i64 %r0123456, %b7
  ret i64 %r
}

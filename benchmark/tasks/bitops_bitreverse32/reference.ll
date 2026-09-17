define i32 @kernel(i32 %x) {
entry:
  %s1l = shl i32 %x, 1
  %s1la = and i32 %s1l, -1431655766
  %s1r = lshr i32 %x, 1
  %s1ra = and i32 %s1r, 1431655765
  %a = or i32 %s1la, %s1ra
  %s2l = shl i32 %a, 2
  %s2la = and i32 %s2l, -858993460
  %s2r = lshr i32 %a, 2
  %s2ra = and i32 %s2r, 858993459
  %b = or i32 %s2la, %s2ra
  %s4l = shl i32 %b, 4
  %s4la = and i32 %s4l, -252645136
  %s4r = lshr i32 %b, 4
  %s4ra = and i32 %s4r, 252645135
  %c = or i32 %s4la, %s4ra
  %s8l = shl i32 %c, 8
  %s8la = and i32 %s8l, -16711936
  %s8r = lshr i32 %c, 8
  %s8ra = and i32 %s8r, 16711935
  %d = or i32 %s8la, %s8ra
  %lo = shl i32 %d, 16
  %hi = lshr i32 %d, 16
  %r = or i32 %lo, %hi
  ret i32 %r
}

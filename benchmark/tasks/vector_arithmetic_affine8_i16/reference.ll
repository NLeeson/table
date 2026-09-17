define <8 x i16> @kernel(<8 x i16> %v) {
entry:
  %x0 = extractelement <8 x i16> %v, i32 0
  %m0 = mul i16 %x0, 5
  %a0 = add i16 %m0, -13
  %x1 = extractelement <8 x i16> %v, i32 1
  %m1 = mul i16 %x1, 5
  %a1 = add i16 %m1, -13
  %x2 = extractelement <8 x i16> %v, i32 2
  %m2 = mul i16 %x2, 5
  %a2 = add i16 %m2, -13
  %x3 = extractelement <8 x i16> %v, i32 3
  %m3 = mul i16 %x3, 5
  %a3 = add i16 %m3, -13
  %x4 = extractelement <8 x i16> %v, i32 4
  %m4 = mul i16 %x4, 5
  %a4 = add i16 %m4, -13
  %x5 = extractelement <8 x i16> %v, i32 5
  %m5 = mul i16 %x5, 5
  %a5 = add i16 %m5, -13
  %x6 = extractelement <8 x i16> %v, i32 6
  %m6 = mul i16 %x6, 5
  %a6 = add i16 %m6, -13
  %x7 = extractelement <8 x i16> %v, i32 7
  %m7 = mul i16 %x7, 5
  %a7 = add i16 %m7, -13
  %o0 = insertelement <8 x i16> poison, i16 %a0, i32 0
  %o1 = insertelement <8 x i16> %o0, i16 %a1, i32 1
  %o2 = insertelement <8 x i16> %o1, i16 %a2, i32 2
  %o3 = insertelement <8 x i16> %o2, i16 %a3, i32 3
  %o4 = insertelement <8 x i16> %o3, i16 %a4, i32 4
  %o5 = insertelement <8 x i16> %o4, i16 %a5, i32 5
  %o6 = insertelement <8 x i16> %o5, i16 %a6, i32 6
  %o7 = insertelement <8 x i16> %o6, i16 %a7, i32 7
  ret <8 x i16> %o7
}

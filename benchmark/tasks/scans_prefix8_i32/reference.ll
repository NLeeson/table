define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %v0 = extractelement <8 x i32> %v, i32 0
  %v1 = extractelement <8 x i32> %v, i32 1
  %v2 = extractelement <8 x i32> %v, i32 2
  %v3 = extractelement <8 x i32> %v, i32 3
  %v4 = extractelement <8 x i32> %v, i32 4
  %v5 = extractelement <8 x i32> %v, i32 5
  %v6 = extractelement <8 x i32> %v, i32 6
  %v7 = extractelement <8 x i32> %v, i32 7

  %p1 = add i32 %v0, %v1
  %p2 = add i32 %p1, %v2
  %p3 = add i32 %p2, %v3
  %p4 = add i32 %p3, %v4
  %p5 = add i32 %p4, %v5
  %p6 = add i32 %p5, %v6
  %p7 = add i32 %p6, %v7

  %r0 = insertelement <8 x i32> poison, i32 %v0, i32 0
  %r1 = insertelement <8 x i32> %r0, i32 %p1, i32 1
  %r2 = insertelement <8 x i32> %r1, i32 %p2, i32 2
  %r3 = insertelement <8 x i32> %r2, i32 %p3, i32 3
  %r4 = insertelement <8 x i32> %r3, i32 %p4, i32 4
  %r5 = insertelement <8 x i32> %r4, i32 %p5, i32 5
  %r6 = insertelement <8 x i32> %r5, i32 %p6, i32 6
  %r7 = insertelement <8 x i32> %r6, i32 %p7, i32 7
  ret <8 x i32> %r7
}

define <4 x i64> @kernel(<4 x i64> %v) {
entry:
  %v0 = extractelement <4 x i64> %v, i32 0
  %v1 = extractelement <4 x i64> %v, i32 1
  %v2 = extractelement <4 x i64> %v, i32 2
  %v3 = extractelement <4 x i64> %v, i32 3
  %p1 = add i64 %v0, %v1
  %p2 = add i64 %p1, %v2
  %p3 = add i64 %p2, %v3
  %o0 = insertelement <4 x i64> poison, i64 %v0, i32 0
  %o1 = insertelement <4 x i64> %o0, i64 %p1, i32 1
  %o2 = insertelement <4 x i64> %o1, i64 %p2, i32 2
  %o3 = insertelement <4 x i64> %o2, i64 %p3, i32 3
  ret <4 x i64> %o3
}

define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %s1 = shufflevector <8 x i32> %v, <8 x i32> undef, <8 x i32> <i32 undef, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5, i32 6>
  %a1 = add <8 x i32> %v, %s1
  %x1 = insertelement <8 x i32> %a1, i32 0, i32 0
  %x1v0 = extractelement <8 x i32> %v, i32 0
  %x1 = insertelement <8 x i32> %a1, i32 %x1v0, i32 0
  %s2 = shufflevector <8 x i32> %x1, <8 x i32> undef, <8 x i32> <i32 undef, i32 undef, i32 0, i32 1, i32 2, i32 3, i32 4, i32 5>
  %a2 = add <8 x i32> %x1, %s2
  %x2a = insertelement <8 x i32> %a2, i32 %x1v0, i32 0
  %x1v1 = extractelement <8 x i32> %x1, i32 1
  %x2 = insertelement <8 x i32> %x2a, i32 %x1v1, i32 1
  %s4 = shufflevector <8 x i32> %x2, <8 x i32> undef, <8 x i32> <i32 undef, i32 undef, i32 undef, i32 undef, i32 0, i32 1, i32 2, i32 3>
  %a4 = add <8 x i32> %x2, %s4
  %x4a = insertelement <8 x i32> %a4, i32 %x1v0, i32 0
  %x2v1 = extractelement <8 x i32> %x2, i32 1
  %x4b = insertelement <8 x i32> %x4a, i32 %x2v1, i32 1
  %x2v2 = extractelement <8 x i32> %x2, i32 2
  %x4c = insertelement <8 x i32> %x4b, i32 %x2v2, i32 2
  %x2v3 = extractelement <8 x i32> %x2, i32 3
  %x4 = insertelement <8 x i32> %x4c, i32 %x2v3, i32 3
  ret <8 x i32> %x4
}

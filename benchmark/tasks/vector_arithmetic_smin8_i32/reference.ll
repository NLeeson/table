define <8 x i32> @kernel(<8 x i32> %a, <8 x i32> %b) {
entry:
  %a0 = extractelement <8 x i32> %a, i32 0
  %b0 = extractelement <8 x i32> %b, i32 0
  %c0 = icmp slt i32 %a0, %b0
  %m0 = select i1 %c0, i32 %a0, i32 %b0
  %a1 = extractelement <8 x i32> %a, i32 1
  %b1 = extractelement <8 x i32> %b, i32 1
  %c1 = icmp slt i32 %a1, %b1
  %m1 = select i1 %c1, i32 %a1, i32 %b1
  %a2 = extractelement <8 x i32> %a, i32 2
  %b2 = extractelement <8 x i32> %b, i32 2
  %c2 = icmp slt i32 %a2, %b2
  %m2 = select i1 %c2, i32 %a2, i32 %b2
  %a3 = extractelement <8 x i32> %a, i32 3
  %b3 = extractelement <8 x i32> %b, i32 3
  %c3 = icmp slt i32 %a3, %b3
  %m3 = select i1 %c3, i32 %a3, i32 %b3
  %a4 = extractelement <8 x i32> %a, i32 4
  %b4 = extractelement <8 x i32> %b, i32 4
  %c4 = icmp slt i32 %a4, %b4
  %m4 = select i1 %c4, i32 %a4, i32 %b4
  %a5 = extractelement <8 x i32> %a, i32 5
  %b5 = extractelement <8 x i32> %b, i32 5
  %c5 = icmp slt i32 %a5, %b5
  %m5 = select i1 %c5, i32 %a5, i32 %b5
  %a6 = extractelement <8 x i32> %a, i32 6
  %b6 = extractelement <8 x i32> %b, i32 6
  %c6 = icmp slt i32 %a6, %b6
  %m6 = select i1 %c6, i32 %a6, i32 %b6
  %a7 = extractelement <8 x i32> %a, i32 7
  %b7 = extractelement <8 x i32> %b, i32 7
  %c7 = icmp slt i32 %a7, %b7
  %m7 = select i1 %c7, i32 %a7, i32 %b7
  %o0 = insertelement <8 x i32> poison, i32 %m0, i32 0
  %o1 = insertelement <8 x i32> %o0, i32 %m1, i32 1
  %o2 = insertelement <8 x i32> %o1, i32 %m2, i32 2
  %o3 = insertelement <8 x i32> %o2, i32 %m3, i32 3
  %o4 = insertelement <8 x i32> %o3, i32 %m4, i32 4
  %o5 = insertelement <8 x i32> %o4, i32 %m5, i32 5
  %o6 = insertelement <8 x i32> %o5, i32 %m6, i32 6
  %o7 = insertelement <8 x i32> %o6, i32 %m7, i32 7
  ret <8 x i32> %o7
}

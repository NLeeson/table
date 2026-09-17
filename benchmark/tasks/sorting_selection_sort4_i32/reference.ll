define <4 x i32> @kernel(<4 x i32> %v) {
entry:
  %a = extractelement <4 x i32> %v, i32 0
  %b = extractelement <4 x i32> %v, i32 1
  %c = extractelement <4 x i32> %v, i32 2
  %d = extractelement <4 x i32> %v, i32 3
  %c0 = icmp slt i32 %a, %b
  %a0 = select i1 %c0, i32 %a, i32 %b
  %b0 = select i1 %c0, i32 %b, i32 %a
  %c1 = icmp slt i32 %c, %d
  %c0v = select i1 %c1, i32 %c, i32 %d
  %d0 = select i1 %c1, i32 %d, i32 %c
  %c2 = icmp slt i32 %a0, %c0v
  %a1 = select i1 %c2, i32 %a0, i32 %c0v
  %c1v = select i1 %c2, i32 %c0v, i32 %a0
  %c3 = icmp slt i32 %b0, %d0
  %b1 = select i1 %c3, i32 %b0, i32 %d0
  %d1 = select i1 %c3, i32 %d0, i32 %b0
  %c4 = icmp slt i32 %b1, %c1v
  %b2 = select i1 %c4, i32 %b1, i32 %c1v
  %c2v = select i1 %c4, i32 %c1v, i32 %b1
  %o0 = insertelement <4 x i32> poison, i32 %a1, i32 0
  %o1 = insertelement <4 x i32> %o0, i32 %b2, i32 1
  %o2 = insertelement <4 x i32> %o1, i32 %c2v, i32 2
  %o3 = insertelement <4 x i32> %o2, i32 %d1, i32 3
  ret <4 x i32> %o3
}

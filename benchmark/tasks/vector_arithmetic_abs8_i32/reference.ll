define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %x0 = extractelement <8 x i32> %v, i32 0
  %n0 = sub i32 0, %x0
  %c0 = icmp slt i32 %x0, 0
  %a0 = select i1 %c0, i32 %n0, i32 %x0
  %x1 = extractelement <8 x i32> %v, i32 1
  %n1 = sub i32 0, %x1
  %c1 = icmp slt i32 %x1, 0
  %a1 = select i1 %c1, i32 %n1, i32 %x1
  %x2 = extractelement <8 x i32> %v, i32 2
  %n2 = sub i32 0, %x2
  %c2 = icmp slt i32 %x2, 0
  %a2 = select i1 %c2, i32 %n2, i32 %x2
  %x3 = extractelement <8 x i32> %v, i32 3
  %n3 = sub i32 0, %x3
  %c3 = icmp slt i32 %x3, 0
  %a3 = select i1 %c3, i32 %n3, i32 %x3
  %x4 = extractelement <8 x i32> %v, i32 4
  %n4 = sub i32 0, %x4
  %c4 = icmp slt i32 %x4, 0
  %a4 = select i1 %c4, i32 %n4, i32 %x4
  %x5 = extractelement <8 x i32> %v, i32 5
  %n5 = sub i32 0, %x5
  %c5 = icmp slt i32 %x5, 0
  %a5 = select i1 %c5, i32 %n5, i32 %x5
  %x6 = extractelement <8 x i32> %v, i32 6
  %n6 = sub i32 0, %x6
  %c6 = icmp slt i32 %x6, 0
  %a6 = select i1 %c6, i32 %n6, i32 %x6
  %x7 = extractelement <8 x i32> %v, i32 7
  %n7 = sub i32 0, %x7
  %c7 = icmp slt i32 %x7, 0
  %a7 = select i1 %c7, i32 %n7, i32 %x7
  %o0 = insertelement <8 x i32> poison, i32 %a0, i32 0
  %o1 = insertelement <8 x i32> %o0, i32 %a1, i32 1
  %o2 = insertelement <8 x i32> %o1, i32 %a2, i32 2
  %o3 = insertelement <8 x i32> %o2, i32 %a3, i32 3
  %o4 = insertelement <8 x i32> %o3, i32 %a4, i32 4
  %o5 = insertelement <8 x i32> %o4, i32 %a5, i32 5
  %o6 = insertelement <8 x i32> %o5, i32 %a6, i32 6
  %o7 = insertelement <8 x i32> %o6, i32 %a7, i32 7
  ret <8 x i32> %o7
}

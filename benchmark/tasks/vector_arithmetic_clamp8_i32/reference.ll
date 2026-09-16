define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %x0 = extractelement <8 x i32> %v, i32 0
  %m0 = mul i32 %x0, 3
  %a0 = add i32 %m0, 7
  %l0 = icmp slt i32 %a0, -100
  %c0a = select i1 %l0, i32 -100, i32 %a0
  %h0 = icmp sgt i32 %c0a, 100
  %c0 = select i1 %h0, i32 100, i32 %c0a

  %x1 = extractelement <8 x i32> %v, i32 1
  %m1 = mul i32 %x1, 3
  %a1 = add i32 %m1, 7
  %l1 = icmp slt i32 %a1, -100
  %c1a = select i1 %l1, i32 -100, i32 %a1
  %h1 = icmp sgt i32 %c1a, 100
  %c1 = select i1 %h1, i32 100, i32 %c1a

  %x2 = extractelement <8 x i32> %v, i32 2
  %m2 = mul i32 %x2, 3
  %a2 = add i32 %m2, 7
  %l2 = icmp slt i32 %a2, -100
  %c2a = select i1 %l2, i32 -100, i32 %a2
  %h2 = icmp sgt i32 %c2a, 100
  %c2 = select i1 %h2, i32 100, i32 %c2a

  %x3 = extractelement <8 x i32> %v, i32 3
  %m3 = mul i32 %x3, 3
  %a3 = add i32 %m3, 7
  %l3 = icmp slt i32 %a3, -100
  %c3a = select i1 %l3, i32 -100, i32 %a3
  %h3 = icmp sgt i32 %c3a, 100
  %c3 = select i1 %h3, i32 100, i32 %c3a

  %x4 = extractelement <8 x i32> %v, i32 4
  %m4 = mul i32 %x4, 3
  %a4 = add i32 %m4, 7
  %l4 = icmp slt i32 %a4, -100
  %c4a = select i1 %l4, i32 -100, i32 %a4
  %h4 = icmp sgt i32 %c4a, 100
  %c4 = select i1 %h4, i32 100, i32 %c4a

  %x5 = extractelement <8 x i32> %v, i32 5
  %m5 = mul i32 %x5, 3
  %a5 = add i32 %m5, 7
  %l5 = icmp slt i32 %a5, -100
  %c5a = select i1 %l5, i32 -100, i32 %a5
  %h5 = icmp sgt i32 %c5a, 100
  %c5 = select i1 %h5, i32 100, i32 %c5a

  %x6 = extractelement <8 x i32> %v, i32 6
  %m6 = mul i32 %x6, 3
  %a6 = add i32 %m6, 7
  %l6 = icmp slt i32 %a6, -100
  %c6a = select i1 %l6, i32 -100, i32 %a6
  %h6 = icmp sgt i32 %c6a, 100
  %c6 = select i1 %h6, i32 100, i32 %c6a

  %x7 = extractelement <8 x i32> %v, i32 7
  %m7 = mul i32 %x7, 3
  %a7 = add i32 %m7, 7
  %l7 = icmp slt i32 %a7, -100
  %c7a = select i1 %l7, i32 -100, i32 %a7
  %h7 = icmp sgt i32 %c7a, 100
  %c7 = select i1 %h7, i32 100, i32 %c7a

  %r0 = insertelement <8 x i32> poison, i32 %c0, i32 0
  %r1 = insertelement <8 x i32> %r0, i32 %c1, i32 1
  %r2 = insertelement <8 x i32> %r1, i32 %c2, i32 2
  %r3 = insertelement <8 x i32> %r2, i32 %c3, i32 3
  %r4 = insertelement <8 x i32> %r3, i32 %c4, i32 4
  %r5 = insertelement <8 x i32> %r4, i32 %c5, i32 5
  %r6 = insertelement <8 x i32> %r5, i32 %c6, i32 6
  %r7 = insertelement <8 x i32> %r6, i32 %c7, i32 7
  ret <8 x i32> %r7
}

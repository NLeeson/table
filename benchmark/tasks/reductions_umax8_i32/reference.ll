define i32 @kernel(<8 x i32> %v) {
entry:
  %v0 = extractelement <8 x i32> %v, i32 0
  %v1 = extractelement <8 x i32> %v, i32 1
  %v2 = extractelement <8 x i32> %v, i32 2
  %v3 = extractelement <8 x i32> %v, i32 3
  %v4 = extractelement <8 x i32> %v, i32 4
  %v5 = extractelement <8 x i32> %v, i32 5
  %v6 = extractelement <8 x i32> %v, i32 6
  %v7 = extractelement <8 x i32> %v, i32 7
  %c1 = icmp ugt i32 %v0, %v1
  %r1 = select i1 %c1, i32 %v0, i32 %v1
  %c2 = icmp ugt i32 %r1, %v2
  %r2 = select i1 %c2, i32 %r1, i32 %v2
  %c3 = icmp ugt i32 %r2, %v3
  %r3 = select i1 %c3, i32 %r2, i32 %v3
  %c4 = icmp ugt i32 %r3, %v4
  %r4 = select i1 %c4, i32 %r3, i32 %v4
  %c5 = icmp ugt i32 %r4, %v5
  %r5 = select i1 %c5, i32 %r4, i32 %v5
  %c6 = icmp ugt i32 %r5, %v6
  %r6 = select i1 %c6, i32 %r5, i32 %v6
  %c7 = icmp ugt i32 %r6, %v7
  %r7 = select i1 %c7, i32 %r6, i32 %v7
  ret i32 %r7
}

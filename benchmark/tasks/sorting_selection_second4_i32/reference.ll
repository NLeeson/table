define i32 @kernel(i32 %a, i32 %b, i32 %c, i32 %d) {
entry:
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
  %second = select i1 %c4, i32 %b1, i32 %c1v
  ret i32 %second
}

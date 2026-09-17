define <2 x i32> @kernel(i32 %a, i32 %b, i32 %c, i32 %d) {
entry:
  %ablt = icmp slt i32 %a, %b
  %abmin = select i1 %ablt, i32 %a, i32 %b
  %abmax = select i1 %ablt, i32 %b, i32 %a
  %cdlt = icmp slt i32 %c, %d
  %cdmin = select i1 %cdlt, i32 %c, i32 %d
  %cdmax = select i1 %cdlt, i32 %d, i32 %c
  %mnlt = icmp slt i32 %abmin, %cdmin
  %mn = select i1 %mnlt, i32 %abmin, i32 %cdmin
  %mxgt = icmp sgt i32 %abmax, %cdmax
  %mx = select i1 %mxgt, i32 %abmax, i32 %cdmax
  %o0 = insertelement <2 x i32> poison, i32 %mn, i32 0
  %o1 = insertelement <2 x i32> %o0, i32 %mx, i32 1
  ret <2 x i32> %o1
}

define i32 @kernel(i32 %a, i32 %b, i32 %c) {
entry:
  %ab = icmp slt i32 %a, %b
  %lo = select i1 %ab, i32 %a, i32 %b
  %hi = select i1 %ab, i32 %b, i32 %a
  %hc = icmp slt i32 %hi, %c
  %mid = select i1 %hc, i32 %hi, i32 %c
  %lm = icmp slt i32 %lo, %mid
  %result = select i1 %lm, i32 %mid, i32 %lo
  ret i32 %result
}

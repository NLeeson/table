define i32 @kernel(i32 %a, i32 %b, i32 %c) {
entry:
  %ab = icmp slt i32 %a, %b
  %lo_ab = select i1 %ab, i32 %a, i32 %b
  %hi_ab = select i1 %ab, i32 %b, i32 %a
  %hic = icmp slt i32 %hi_ab, %c
  %mid_candidate = select i1 %hic, i32 %hi_ab, i32 %c
  %lom = icmp slt i32 %lo_ab, %mid_candidate
  %median = select i1 %lom, i32 %mid_candidate, i32 %lo_ab
  ret i32 %median
}

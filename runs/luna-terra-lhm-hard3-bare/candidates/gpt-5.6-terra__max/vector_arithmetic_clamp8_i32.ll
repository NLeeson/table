define <8 x i32> @kernel(<8 x i32> %v) {
entry:
  %m = mul <8 x i32> %v, <i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3>
  %a = add <8 x i32> %m, <i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7>
  %low = icmp slt <8 x i32> %a, <i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100>
  %clamped_low = select <8 x i1> %low, <8 x i32> <i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100, i32 -100>, <8 x i32> %a
  %high = icmp sgt <8 x i32> %clamped_low, <i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100>
  %result = select <8 x i1> %high, <8 x i32> <i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100>, <8 x i32> %clamped_low
  ret <8 x i32> %result
}

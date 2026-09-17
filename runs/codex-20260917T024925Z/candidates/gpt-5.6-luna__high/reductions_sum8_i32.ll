declare i32 @llvm.vector.reduce.add.v8i32(<8 x i32>)

define i32 @kernel(<8 x i32> %v) {
entry:
  %sum = call i32 @llvm.vector.reduce.add.v8i32(<8 x i32> %v)
  ret i32 %sum
}

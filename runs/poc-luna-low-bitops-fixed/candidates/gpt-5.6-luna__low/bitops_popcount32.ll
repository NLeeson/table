declare i32 @llvm.ctpop.i32(i32)

define i32 @kernel(i32 %x) {
entry:
  %r = call i32 @llvm.ctpop.i32(i32 %x)
  ret i32 %r
}

(define var1 '())
(define var2 '())
(define jack
    (begin
        (set! var1 (cons 5 var1))
        (set! var2 #f)
        12345))
(print var1)
(print var2)
(print jack)

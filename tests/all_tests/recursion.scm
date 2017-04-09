(define (repeat-print times sym)
    (if (> times 0)
        (begin
            (print sym)
            (repeat-print (- times 1) sym))))

(repeat-print 3 'hello)

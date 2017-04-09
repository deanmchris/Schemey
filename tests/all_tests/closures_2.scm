(define (make-withdraw balance)
    (lambda (amount)
        (if (>= balance amount)
            (begin (set! balance (- balance amount))
                    balance)
            "no-funds")))

(define wd1 (make-withdraw 100))
(define wd2 (make-withdraw 500))

(print (wd1 20))
(print (wd2 700))
(print (wd1 200))
(print (wd2 100))

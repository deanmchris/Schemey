(define (even? n)
    (if (= n 0)
        #t
        (odd? (- n 1))))

(define (odd? n)
    (if (= n 0)
        #f
        (even? (- n 1))))

(print (even? 5))
(print (odd? 5))
(print (even? 52))
(print (odd? 52))

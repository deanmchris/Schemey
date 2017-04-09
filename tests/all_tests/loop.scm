; Iterative prime-checking, the stupidest kind possible (dividing
; by numbers until num - 1)
;
(define (divides k n)
    (= (modulo n k) 0))

(define (primecheck num)
    (define (auxprimecheck divisor)
        (cond 
            ((= divisor num) #t)
            ((divides divisor num) #f)
            (else (auxprimecheck (+ 1 divisor)))))
    (auxprimecheck 2))

(print (primecheck 17))
(print (primecheck 49))
(print (primecheck 51))
(print (primecheck 71))
(print (primecheck 101))
(print (primecheck 102))

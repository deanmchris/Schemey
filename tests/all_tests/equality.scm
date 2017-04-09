(print (eqv? 1 2))
(print (eqv? "a" 'a))
(print (eqv? '() '()))

(define a '(1 2 3))
(print (eqv? a '(1 2 3)))
(print (eqv? a a))
(print (eqv? '(1 2 3) '(1 2 3)))

(define b 'b)
(print (eqv? b 'b))
(print (eqv? b b))
(print (eqv? 'b 'b))


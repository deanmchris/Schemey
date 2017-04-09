(define (make-multiplier a)
	(lambda (b) 
		(* b a)))

(define mul2 (make-multiplier 2))
(define mul3 (make-multiplier 3))

(print (mul2 2))
(print (mul3 5))

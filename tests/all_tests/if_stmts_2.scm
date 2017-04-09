(define (cadr lst)
	(car (cdr lst)))

(print (if (car (cons #f #t)) 1 2))
(print (if (car '(#f #t)) 1 2))
(print (if (cdr (cons #f #t)) 1 2))
(print (if (cadr '(#f #t)) 1 2))

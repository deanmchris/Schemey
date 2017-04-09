; everything except #f is true

(define a 
	(if #f
		1
		2))
(define b
	(if '(abc)
		3
		4))
(define c
	(if ""
		5
		6))
(define d
	(if '()
		7
		8))
(define e
	(if 0
		9
		10))

(print a)
(print b)
(print c)
(print d)
(print e)

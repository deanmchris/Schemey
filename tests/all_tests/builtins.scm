(define (type obj) 
	(cond ((null? obj) "null")
				((number? obj) "number")
				((symbol? obj) "symbol")
        ((boolean? obj) "boolean")
        ((pair? obj) "pair")
        ((string? obj) "string")))

(print (type 'abc))
(print (type 12))
(print (type "def"))
(print (type (cons 1 2)))
(print (type '()))
(print (type (list 1 2)))



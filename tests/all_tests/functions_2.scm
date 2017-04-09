(define (foldr func end lst)
  (if (null? lst)
      end
      (func (car lst) (foldr func end (cdr lst)))))

(define (map func lst)
	(foldr (lambda (x y)
		(cons (func x) y))
	'()
	lst))


(print (map string-length '("eggs" "elephant" "truck")))
(print (map (lambda (n) (* n n)) '(1 2 3 4 5)))
(print (map number? '(1 "A" 3 '( 1 2 3))))

(define (list-length lst)
    (if (null? lst)
        0
        (+ 1 (list-length (cdr lst)))))

(define (make-range-list num)
    (if (= 0 num)
      '()
      (cons num (make-range-list (- num 1)))))

(define l1 (make-range-list 500))
(print (list-length l1))
(define l2 (make-range-list 800))
(print (list-length l2))

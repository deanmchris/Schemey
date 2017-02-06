; This file implements several test programs for the interpreter
; to execute. 

(print '-------------------simple-arithmetic-------------------)

; simple arithmetic
(print (+ 1 2 3 4 5))
(print (- 20 10))
(print (* 3 2))
(print (/ 24 6))

(print '-------------------complex-arithmetic-------------------)

;complex arithmetic
(print (+ 1 3 67 (- 55 34 (* 33 81 (/ 96 24)))))
(print (/ 99 (* 3 ( + 6 5))))
(print (% 64 (* 2 (* 8 (+ 2 2)))))

(print '-----------------comparision-arithmetic-----------------)

;comparision operators
(print (= 1 1))
(print (> 4 3))
(print (< 3 4))
(print (>= 11 10))
(print (<= 10 11))
(print (and 1 1))
(print (or () 1))
(print (not #f))

(print '---------------------truth-testing---------------------)

;truth testing
(print (eq? 1 2))
(print (eqv? 1 1))
(print (pair? (cons 1 2)))
(print (zero? 1))
(print (boolean? #t))
(print symbol? 'a)
(print number? 10)
(print (null? ()))

(print '--------------------list-operations--------------------)

; list operations
(define x (list 1 2 3 4 5 6 7 8 9 10))
(print x)

(print (car x))
(print (car (cdr x)))
(print (cons 1 x))

(print (set-car! 25 x))
(print x)

(print (set-cdr! (list 24 23 22 21 20) x))
(print x)

(print '-----------------------closures-----------------------)

; closures
(define square (lambda (n) (* n n)))
(print (square 12))
(print (square (square 5)))

(define pow (lambda (n e) (* n e)))
(print (pow 5 2))
(print (pow 10 3))

(define say-hello (lambda () (print 'Hello)))
(say-hello)
(define (account balance)
  ; withdraw from account
  (define (withdraw amount)
    (set! balance (- balance amount))
    balance)
  ; deposit to account
  (define (deposit amount)
    (set! balance (+ balance amount)))
  ; dispatch commands
  (define (dispatch request)
    (cond
      ((eqv? request "withdraw") withdraw)
      ((eqv? request "deposit") deposit)
      ((eqv? request "query") balance)
      (else "unknown request")))
  dispatch)
    
(define acc1 (account 1200))
(define acc2 (account 1200))

(print ((acc1 "withdraw") 249))
((acc2 "deposit") 272)
(print (acc2 "query"))
(print (acc1 "query"))
(print (acc1 "foo"))

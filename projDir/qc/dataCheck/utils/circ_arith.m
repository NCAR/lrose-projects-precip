function v = circ_arith(val,nyq)

v = mod(val+nyq,2*nyq)-nyq;
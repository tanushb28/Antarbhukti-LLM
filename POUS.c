void SFC_PROGRAM_init__(SFC_PROGRAM *data__, BOOL retain) {
  __INIT_VAR(data__->INIT_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->VALIDATEINPUT_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->VALIDATIONERROR_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->CHECK_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->ADD_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->INC_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SAFEABORT_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->END_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SAFETYCHECKINPUT_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SAFETYERROR_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->SAFETYLOG_ACTIVE,__BOOL_LITERAL(FALSE),retain)
  __INIT_VAR(data__->TRI,0,retain)
  __INIT_VAR(data__->I,0,retain)
  __INIT_VAR(data__->N,0,retain)
  __INIT_VAR(data__->INIT,0,retain)
  __INIT_VAR(data__->LOOP_COUNT,0,retain)
  __INIT_VAR(data__->MAX_N,0,retain)
  __INIT_VAR(data__->MAX_ITERATIONS,0,retain)
}

// Code part
void SFC_PROGRAM_body__(SFC_PROGRAM *data__) {
  // Initialise TEMP variables

  if (!(__GET_VAR(data__->INIT_ACTIVE,))) {
    __SET_VAR(data__->,INIT_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if (__GET_VAR(data__->INIT_ACTIVE,)) {
    __SET_VAR(data__->,TRI,,0);
    __SET_VAR(data__->,I,,1);
    __SET_VAR(data__->,LOOP_COUNT,,0);
  };
  if (__GET_VAR(data__->VALIDATIONERROR_ACTIVE,)) {
    __SET_VAR(data__->,TRI,,0);
  };
  if (__GET_VAR(data__->ADD_ACTIVE,)) {
    __SET_VAR(data__->,TRI,,(__GET_VAR(data__->TRI,) + __GET_VAR(data__->I,)));
  };
  if (__GET_VAR(data__->INC_ACTIVE,)) {
    __SET_VAR(data__->,I,,(__GET_VAR(data__->I,) + 1));
    __SET_VAR(data__->,LOOP_COUNT,,(__GET_VAR(data__->LOOP_COUNT,) + 1));
  };
  if (__GET_VAR(data__->SAFEABORT_ACTIVE,)) {
    __SET_VAR(data__->,TRI,,0);
  };
  if (__GET_VAR(data__->SAFETYERROR_ACTIVE,)) {
    __SET_VAR(data__->,TRI,,0);
  };
  if ((__GET_VAR(data__->INIT_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,INIT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYCHECKINPUT_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->SAFETYCHECKINPUT_ACTIVE,) && ((__GET_VAR(data__->N,) < 0) || (__GET_VAR(data__->N,) > __GET_VAR(data__->MAX_N,))))) {
    __SET_VAR(data__->,SAFETYCHECKINPUT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYERROR_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->SAFETYCHECKINPUT_ACTIVE,) && ((__GET_VAR(data__->N,) >= 0) && (__GET_VAR(data__->N,) <= __GET_VAR(data__->MAX_N,))))) {
    __SET_VAR(data__->,SAFETYCHECKINPUT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,VALIDATEINPUT_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->VALIDATEINPUT_ACTIVE,) && ((__GET_VAR(data__->N,) >= 0) && (__GET_VAR(data__->N,) <= __GET_VAR(data__->MAX_N,))))) {
    __SET_VAR(data__->,VALIDATEINPUT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,CHECK_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->VALIDATEINPUT_ACTIVE,) && ((__GET_VAR(data__->N,) < 0) || (__GET_VAR(data__->N,) > __GET_VAR(data__->MAX_N,))))) {
    __SET_VAR(data__->,VALIDATEINPUT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,VALIDATIONERROR_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->VALIDATIONERROR_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,VALIDATIONERROR_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYLOG_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->CHECK_ACTIVE,) && (__GET_VAR(data__->I,) <= __GET_VAR(data__->N,)))) {
    __SET_VAR(data__->,CHECK_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,ADD_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->ADD_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,ADD_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,INC_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->INC_ACTIVE,) && (__GET_VAR(data__->LOOP_COUNT,) <= __GET_VAR(data__->MAX_ITERATIONS,)))) {
    __SET_VAR(data__->,INC_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,CHECK_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->INC_ACTIVE,) && (__GET_VAR(data__->LOOP_COUNT,) > __GET_VAR(data__->MAX_ITERATIONS,)))) {
    __SET_VAR(data__->,INC_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFEABORT_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->SAFEABORT_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,SAFEABORT_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYLOG_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->CHECK_ACTIVE,) && (__GET_VAR(data__->I,) > __GET_VAR(data__->N,)))) {
    __SET_VAR(data__->,CHECK_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYLOG_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->SAFETYERROR_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,SAFETYERROR_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,SAFETYLOG_ACTIVE,,__BOOL_LITERAL(TRUE));
  };
  if ((__GET_VAR(data__->SAFETYLOG_ACTIVE,) && __BOOL_LITERAL(TRUE))) {
    __SET_VAR(data__->,SAFETYLOG_ACTIVE,,__BOOL_LITERAL(FALSE));
    __SET_VAR(data__->,END_ACTIVE,,__BOOL_LITERAL(TRUE));
  };

  goto __end;

__end:
  return;
} // SFC_PROGRAM_body__() 






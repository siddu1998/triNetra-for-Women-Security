//
// ELL SWIG header for module model
//

#pragma once

#if !defined(SWIG)
#include "CallbackInterface.h"
//
// ELL header for module model
//

#pragma once

#include <stdint.h>

#if defined(__cplusplus)
extern "C"
{
#endif // defined(__cplusplus)

//
// Types
//

#if !defined(ELL_TensorShape)
#define ELL_TensorShape

typedef struct TensorShape
{
    int32_t rows;
    int32_t columns;
    int32_t channels;
} TensorShape;

#endif // !defined(ELL_TensorShape)

//
// Functions
//

// Input size: 1
// Output size: 1000
void model_Predict(void* context, double* input0, float* output0);

double model_GetTicksUntilNextInterval(double currentTime);

double model_GetLagThreshold();

double model_GetStepInterval();

void model_Reset();

int32_t model_GetInputSize();

int32_t model_GetOutputSize();

int32_t model_GetNumNodes();

void model_GetInputShape(int32_t index, TensorShape* shape);

void model_GetOutputShape(int32_t index, TensorShape* shape);

#if defined(__cplusplus)
} // extern "C"
#endif // defined(__cplusplus)

#endif // !defined(SWIG)

void model_Predict(void* context, const std::vector<double>& input, std::vector<float>& output);
void model_Reset();

#if !defined(SWIG)
void model_Predict(void* context, const std::vector<double>& input, std::vector<float>& output)
{
    model_Predict(context, const_cast<double*>(&input[0]), &output[0]);
}
#endif // !defined(SWIG)

// Predictor class

class model_Predictor : public ell::api::CallbackForwarder<float, float>
{
public:
    model_Predictor() = default;
    virtual ~model_Predictor() = default;
};

#ifndef SWIG

extern "C"
{

int8_t model_InputCallback(void* context, float* input)
{
    auto predictor = reinterpret_cast<model_Predictor*>(context);
    return static_cast<int8_t>(predictor->InvokeInput(input));
}

void model_OutputCallback(void* context, float* output)
{
    auto predictor = reinterpret_cast<model_Predictor*>(context);
    predictor->InvokeOutput(output);
}

void model_LagNotification(void* context, double lag)
{
    auto predictor = reinterpret_cast<model_Predictor*>(context);
    predictor->InvokeLagNotification(lag);
}

} // extern "C"

#endif // SWIG


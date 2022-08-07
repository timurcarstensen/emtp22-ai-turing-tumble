/*
 * MIT License
 *
 * Bug+ Interpreter
 * Copyright (c) 2022 Christian Bartelt
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package de.bugplus.development;

import java.util.ArrayList;
import java.util.List;

/**
 * @Author Christian Bartelt
 * @Date 27.01.22 22:18
 * @Version 0.0.1
 */
class BugplusInterfaceImpl implements BugplusInterface {

    final private List<BugplusDataInPin> dataInputPins = new ArrayList<>();
    private BugplusDataOutPin dataOutputPin;

    private BugplusControlInPin controlInputPin;
    final private List<BugplusControlOutPin> controlOutputPins = new ArrayList<>();
    final private List<BugplusJOINControlInstance> controlReturnNodes = new ArrayList<>();
    private int internalState;
    private int callCounter;


    private BugplusInterfaceImpl() {
    }

    BugplusInterfaceImpl(int numDataIns, int numControlOuts, BugplusInstance instance) {

        this();

        this.dataOutputPin = BugplusDataOutPin.getInstance();

        for (int i = 0; i < numDataIns; i++) {
            this.dataInputPins.add(i, BugplusDataInPin.getInstance());
        }

        for (int i = 0; i < numControlOuts; i++) {

            BugplusControlOutPin controlOutPin = BugplusControlOutPin.getInstance();
            this.controlOutputPins.add(i, controlOutPin);
            this.controlReturnNodes.add(i, BugplusJOINControlInstance.getInterfaceControlOutNode(controlOutPin));
        }

        this.internalState = 0;
        this.callCounter = 0;
    }


    @Override
    public void setDataInputs(BugplusDataInPin internalDataInPin, int indexExternalDataInPin) {

        if (indexExternalDataInPin < this.dataInputPins.size()) {
            this.dataInputPins.set(indexExternalDataInPin, internalDataInPin);
        } else {
            System.out.println("Error: The index to connect the data-in-pin is out of bounds of permitted data inputs.");
        }
    }


    @Override
    public void setDataOutputPin(BugplusDataOutPin dataOutPin) {
        this.dataOutputPin = dataOutPin;
    }

    @Override
    public void setControlInput(BugplusControlInPin controlInPin) {
        this.controlInputPin = controlInPin;
    }


    @Override
    public void setControlOutputs(BugplusControlOutPin internalControlOutPin, int indexExternalControlOutPin) {

        BugplusJOINControlInstance returnNode = this.controlReturnNodes.get(indexExternalControlOutPin);
        internalControlOutPin.setFlowTarget(returnNode.getControlIn());
    }

    @Override
    public List<BugplusDataInPin> getDataInputs() {
        return this.dataInputPins;
    }

    @Override
    public BugplusDataOutPin getDataOutput() {
        return this.dataOutputPin;
    }

    @Override
    public List<BugplusControlOutPin> getControlOutputs() {
        return this.controlOutputPins;
    }

    @Override
    public BugplusControlInPin getControlInput() {
        return this.controlInputPin;
    }

    @Override
    public int getInternalState() {
        return this.internalState;
    }

    @Override
    public void setInternalState(int internalState) {
        this.internalState = internalState;
    }

    @Override
    public int getCallCounter() {
        return this.callCounter;
    }

    @Override
    public void setCallCounter(int callCounter) {
        this.callCounter = callCounter;
    }

}


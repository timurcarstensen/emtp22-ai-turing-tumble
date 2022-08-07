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

import de.bugplus.specification.BugplusSpecification;

import java.util.List;

/**
 * @Author Christian Bartelt
 * @Date 25.01.22 18:55
 * @Version 0.0.1
 */
abstract class AbstractBugplusInstance implements BugplusInstance {

    private BugplusImplementation impl;
    private BugplusInterface bugplusIF;


    protected void createInterface(int numDataIn, int numControlOut) {
        this.bugplusIF = BugplusInterface.getInstance(numDataIn, numControlOut, this);
    }


    @Override
    final public BugplusImplementation getImplementation() {
        return this.impl;
    }

    @Override
    final public void setImplementation(BugplusImplementation implementation) {
        this.impl = implementation;
    }

    @Override
    public BugplusSpecification getSpecification() {
        return this.getImplementation().getSpecification();
    }


    @Override
    public BugplusInterface getInterface() {
        return this.bugplusIF;
    }

    @Override
    public BugplusControlInPin getControlIn() {
        return this.getInterface().getControlInput();
    }

    @Override
    public List<BugplusControlOutPin> getControlOuts() {

        return this.getInterface().getControlOutputs();
    }

    @Override
    public List<BugplusDataInPin> getDataInputs() {
        return this.getInterface().getDataInputs();
    }

    @Override
    public BugplusDataOutPin getDataOut() {
        return this.getInterface().getDataOutput();
    }

    @Override
    public void setInputValue(int indexDataInPinIF, int value) {

        List<BugplusDataInPin> dataInPins = this.getInterface().getDataInputs();

        if (dataInPins.size() > indexDataInPinIF) {

            BugplusDataInPin pin = dataInPins.get(indexDataInPinIF);
            BugplusVariable var = pin.getVariable();

            if (var != null) {
                var.setValue(value);
            } else {
                pin.setVariable(BugplusVariable.getInstance(value));
            }

            pin.updateInterfaceInputs();
            //this.getInterface().setInternalState(value);
        } else {
            System.out.println("Error: Cannot set interface input because of index is out of bounds.");
        }
    }

    @Override
    public int getOutputValue() {

        BugplusVariable var = this.getInterface().getDataOutput().getVariable();

        if (var == null) {
            System.out.println("Error: Cannot return an output value because no output value was connected by the interface.");
        }

        return var.getValue();
    }


    //Tobi
    @Override
    public int getInternalState() {
        return this.getInterface().getInternalState();
    }

    @Override
    public void setInternalState(int internalState) {
        this.getInterface().setInternalState(internalState);
        this.getInterface().getDataInputs().get(0).getVariable().setValue(internalState);
        //System.out.println("Internal State "  + internalState);
    }
    @Override
    public BugplusProgramInstanceImpl getInstanceImpl(){
        return (BugplusProgramInstanceImpl) this;
    }

    @Override
    public int getCallCounter() {
        return this.getInterface().getCallCounter();
    }

    @Override
    public void setCallCounter(int callCounter) {
        this.getInterface().setCallCounter(callCounter);
    }


}

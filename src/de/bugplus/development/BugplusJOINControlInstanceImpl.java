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
 * @Date 28.01.22 18:23
 * @Version 0.0.1
 */
final class BugplusJOINControlInstanceImpl extends AbstractBugplusInstance implements BugplusJOINControlInstance {

    private BugplusControlInPin controlInPin;
    private BugplusControlOutPin controlOutPin;

    BugplusJOINControlInstanceImpl(BugplusControlOutPin controlOutputPin) {

        this.controlInPin = new BugplusControlInPinImpl(this);
        this.controlOutPin = controlOutputPin;
    }


    @Override
    public void execute() {

        this.controlOutPin.execute();
    }

    @Override
    public BugplusControlInPin getControlIn() {
        return this.controlInPin;
    }

    @Override
    public List<BugplusControlOutPin> getControlOuts() {

        List<BugplusControlOutPin> controlOuts = new ArrayList<>();
        controlOuts.add(this.controlOutPin);

        return controlOuts;
    }

    @Override
    public List<BugplusDataInPin> getDataInputs() {
        return new ArrayList<BugplusDataInPin>();
    }

    @Override
    public void unsetPins() {

    }

    @Override
    public BugplusInterface getInterface() {
        return BugplusInterface.getInstance(0,1,this);
    }



}

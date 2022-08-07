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

/**
 * @Author Christian Bartelt
 * @Date 27.01.22 21:40
 * @Version 0.0.1
 */
class BugplusControlOutPinImpl implements BugplusControlOutPin {

    protected BugplusControlInPin controlTarget = null;

    BugplusControlOutPinImpl() {}

    BugplusControlOutPinImpl(BugplusControlInPin controlFlowTarget) {

        this();
        this.controlTarget = controlFlowTarget;
    }

    @Override
    public void setFlowTarget(BugplusControlInPin controlInPin) {
        this.controlTarget = controlInPin;
    }

    @Override
    public BugplusControlInPin getFlowTarget() {

        return this.controlTarget;
    }

    @Override
    public void unsetFlowTarget() {
        this.controlTarget = null;
    }

    @Override
    public void execute() {

        if (this.controlTarget != null) {
            this.controlTarget.execute(); }
        else {
            // changed by tsesterh and romanhess98
            //System.out.println("Bug+ program has been terminated!");
        }
    }
}

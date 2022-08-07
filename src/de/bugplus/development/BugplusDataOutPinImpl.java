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
 * @Date 26.01.22 22:44
 * @Version 0.0.1
 */
final class BugplusDataOutPinImpl extends AbstractBugplusDataPin implements BugplusDataOutPin {

    private BugplusDataOutPin interfaceOutput;

    BugplusDataOutPinImpl() {
        this.setVariable(BugplusVariable.getInstance());
    }

    @Override
    public void addDataOutputToInterface(BugplusDataOutPin internalDataOutToConnect) {

        if (internalDataOutToConnect.getVariable() == null) {
            internalDataOutToConnect.setVariable(BugplusVariable.getInstance()); }

        this.interfaceOutput = internalDataOutToConnect;
        internalDataOutToConnect.setConnected();
    }

    @Override
    public void updateInterfaceOutput() {

        if (this.interfaceOutput != null) {
            this.interfaceOutput.getVariable().setValue(this.getVariable().getValue());

            if (this.interfaceOutput.isConnected()) {
                this.interfaceOutput.updateInterfaceOutput();
            }
        }
    }

    @Override
    public void connect(BugplusDataInPin dataInPin) {

        this.connect(dataInPin, this);
    }

    @Override
    public void unsubscribe() {
        this.getVariable().getWriters().remove(this);
    }

    public void setVariable(BugplusVariable variable) {

        variable.addWriter(this);
        super.setVariable(variable);
    }
}

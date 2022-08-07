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
 * @Date 23.01.22 21:37
 * @Version 0.0.1
 */
abstract class AbstractBugplusDataPin implements BugplusDataPin {

    private BugplusVariable variable;
    protected boolean connected = false;

    @Override
    public void setConnected() {
        this.connected = true; }

    @Override
    public boolean isConnected() {

        return this.connected;
    }


    static void connect(BugplusDataInPin dataInPin, BugplusDataOutPin dataOutPin) {

        BugplusVariable variableTarget = dataInPin.getVariable();
        BugplusVariable variableSource = dataOutPin.getVariable();


        if (variableTarget != null) {
            if (variableSource != null) {

                dataOutPin.getVariable().addAllReaders(variableTarget.getReaders());
                dataOutPin.getVariable().addAllWriters(variableTarget.getWriters());

                for (BugplusDataInPin dataInReader : variableTarget.getReaders()) {
                    dataInReader.setVariable(dataOutPin.getVariable()); }

                for (BugplusDataOutPin dataInWriter : variableTarget.getWriters()) {
                    dataInWriter.setVariable(dataOutPin.getVariable()); }

                dataInPin.setVariable(dataOutPin.getVariable());
            }

            dataOutPin.setVariable(dataInPin.getVariable()); }

        else {
            if (variableSource != null) {
                dataInPin.setVariable(dataOutPin.getVariable()); }

            else {
                dataInPin.setVariable(new BugplusVariableImpl(dataInPin, dataOutPin));
                dataOutPin.setVariable(dataInPin.getVariable()); }
        }

        dataInPin.setConnected();

    }

    /*Maybe unnecessary because automatically processed by the garbage collection*/
    abstract public void unsubscribe();

    public void disconnect() {
        /*Maybe unnecessary because automatically processed by the garbage collection*/
        this.unsubscribe();

        this.variable = null;
    }

    @Override
    public BugplusVariable getVariable() {
        return this.variable;
    }

    @Override
    public void setVariable(BugplusVariable variable) {
        this.variable = variable;
    }

}

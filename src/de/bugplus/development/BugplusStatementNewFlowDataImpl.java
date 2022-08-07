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
 * @Date 05.02.22 11:14
 * @Version 0.0.1
 */
final class BugplusStatementNewFlowDataImpl implements BugplusStatementNewFlowData {

    private String sourceBugID;
    private String targetBugID;
    private int indexDataIn;

    private BugplusStatementNewFlowDataImpl() {}

    BugplusStatementNewFlowDataImpl(String idSourceBug, String idTargetBug, int indexDataIn) {

        this.sourceBugID = idSourceBug;
        this.targetBugID = idTargetBug;
        this.indexDataIn = indexDataIn;
    }

    @Override
    public void apply(BugplusProgramInstance instance) {

        BugplusDataOutPin dataOutPin = instance.getBugs().get(this.sourceBugID).getDataOut();
        BugplusDataInPin dataInPin = instance.getBugs().get(this.targetBugID).getDataInputs().get(indexDataIn);

        dataOutPin.connect(dataInPin);
    }
}

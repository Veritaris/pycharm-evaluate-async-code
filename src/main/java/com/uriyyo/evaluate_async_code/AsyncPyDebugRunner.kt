package com.uriyyo.evaluate_async_code

import com.intellij.execution.configurations.GeneralCommandLine
import com.intellij.execution.configurations.ParamsGroup
import com.intellij.openapi.project.Project
import com.jetbrains.python.debugger.PyDebugRunner
import com.jetbrains.python.run.PythonCommandLineState
import com.jetbrains.python.sdk.PythonSdkUtil

class AsyncPyDebugRunner : PyDebugRunner() {

    override fun configureDebugParameters(
            project: Project,
            debugParams: ParamsGroup,
            pyState: PythonCommandLineState,
            cmd: GeneralCommandLine
    ) {
        pyState.sdk?.whenSupport {
            if (!PythonSdkUtil.isRemote(pyState.sdk)) {
                debugParams.addPyDevAsyncWork()
            }
        }

        super.configureDebugParameters(project, debugParams, pyState, cmd)
    }

}
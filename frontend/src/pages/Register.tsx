import { useAuth } from '../context/AuthContext.tsx';
import RegForm from '../funcs/registration_utils/reg_form.tsx';
import VerForm from '../funcs/registration_utils/verif.tsx';

const Register = () => {
    const {
        user
    } = useAuth();

    if (user?.verified === false) {
        return <VerForm />;
    }

    // Step 1: Registration form
    if (user?.verified === undefined) {
        return <RegForm />;
    }
};

export default Register;

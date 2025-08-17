def calc(x, y):
    # This function adds two numbers
    return x + y

def process_data(data):
    # Process the data
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result

class UserManager:
    def __init__(self):
        self.users = []
    
    def find_user_by_role_and_status_and_department(self, role, status, department, min_age, max_age, location, permissions):
        # This is a very long function that does too many things
        # First check role
        filtered_by_role = []
        for u in self.users:
            if u.role == role:
                filtered_by_role.append(u)
        
        # Then check status  
        filtered_by_status = []
        for u in filtered_by_role:
            if u.status == status:
                filtered_by_status.append(u)
        
        # Then check department
        filtered_by_dept = []
        for u in filtered_by_status:
            if u.department == department:
                filtered_by_dept.append(u)
        
        # Then check age range
        filtered_by_age = []
        for u in filtered_by_dept:
            if min_age <= u.age <= max_age:
                filtered_by_age.append(u)
        
        # Then check location
        filtered_by_location = []
        for u in filtered_by_age:
            if u.location == location:
                filtered_by_location.append(u)
        
        # Finally check permissions
        final_result = []
        for u in filtered_by_location:
            if u.permissions == permissions:
                final_result.append(u)
        
        return final_result